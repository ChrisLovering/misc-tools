require 'bindata'
require 'benchmark'
require 'win32/registry'
require 'io/console'

class GGPK
	class UTF16String < BinData::String
		def snapshot
			super.force_encoding('UTF-16LE')
		end
	end

	class RecordBase < BinData::Record
		endian :little
		uint32 :record_length
		string :tag, :length => 4
	end

	class GrindingGearRecord < BinData::Record
		endian :little
		record_base :base
		uint32 :child_count, :value => lambda { children.length }
		array :children, :type => :uint64, :initial_length => :child_count
	end

	class DirectoryEntry < BinData::Record
		endian :little
		uint32 :timestamp
		uint64 :absolute_offset
	end

	class FileRecord < BinData::Record
		endian :little
		uint32 :name_length, :value => lambda { name.length }
		string :digest, :length => 32 # hash of the following data
		utf16_string :name, :read_length => lambda { name_length * 2 }
		
		def utf8_name
			name.encode('UTF-8').chomp("\0")
		end
	end

	class DirectoryRecord < BinData::Record
		endian :little
		uint32 :name_length, :value => lambda { name.length }
		uint32 :child_count, :value => lambda { children.length }
		string :digest, :length => 32
		utf16_string :name, :read_length => lambda { name_length * 2 }
		array :children, :type => :directory_entry, :initial_length => :child_count
		
		def utf8_name
			name.encode('UTF-8').chomp("\0")
		end
	end

	class FreeRecord < BinData::Record
		endian :little
		uint64 :next_record
	end

	def initialize(file)
		@file = file
		@root = GrindingGearRecord.read(@file)
		@free_space = 0
		raise "Invalid input file" unless @root.base.tag == "GGPK"
	end
	
	def traverse_children(path, children)
		children.each do |child|
			@file.pos = child
			base = RecordBase.read(@file)
			
			if base.tag == 'PDIR'
				dir = DirectoryRecord.read(@file)
				traverse_children(path + dir.utf8_name + '/', dir.children.map(&:absolute_offset))
			elsif base.tag == 'FILE'
				file = FileRecord.read(@file)
				puts path + file.utf8_name
			elsif base.tag == 'FREE'
				@free_space += base.record_length - base.num_bytes
			else
				raise "Invalid tag #{base.tag}"
			end
		end
	end

	def list
		traverse_children('', @root.children)
		puts @free_space
	end
	
	def defragment(other)
		@dest = other
		
		dest_root = GrindingGearRecord.new
		dest_root.children = [0] * @root.children.size
		dest_root.base.tag = 'GGPK'
		dest_root.base.record_length = dest_root.num_bytes
		
		@dest.seek dest_root.num_bytes
		
		puts "This will likely take a while..."
		
		dest_root.children = copy_children(@root, @root.children.map do |child|
			entry = DirectoryEntry.new
			entry.absolute_offset = child
			entry
		end).map(&:absolute_offset)
		
		@dest.seek 0
		
		dest_root.write(@dest)
	end
	
	def copy_children(root, children)
		children.map do |child|
			@file.pos = child.absolute_offset
			result = DirectoryEntry.new
			result.timestamp = child.timestamp
			
			base = RecordBase.read(@file)
			
			dest_base = RecordBase.new
			dest_base.tag = base.tag
			
			if base.tag == 'PDIR'
				dir = DirectoryRecord.read(@file)
				
				dest_dir = DirectoryRecord.new
				dest_dir.name = dir.name
				
				children = copy_children(dir, dir.children)
				
				dest_dir.children = children
				
				dest_dir.digest = dir.digest
				
				dest_base.record_length = dest_base.num_bytes + dest_dir.num_bytes
				
				result.absolute_offset = @dest.pos
				
				dest_base.write(@dest)
				dest_dir.write(@dest)
			elsif base.tag == 'FILE'
				
				file = FileRecord.read(@file)
				
				remaining = base.record_length - (base.num_bytes + file.num_bytes)
				
				dest_file = FileRecord.new
				dest_base.record_length = base.record_length
				dest_file.name = file.name
				dest_file.digest = file.digest
				
				result.absolute_offset = @dest.pos
				
				dest_base.write(@dest)
				dest_file.write(@dest)
				
				data = @file.read(remaining)
				@dest.write(data)
			elsif base.tag == 'FREE'
				dest_free = FreeRecord.new
				dest_free.next_record = 0
				
				dest_base.record_length = dest_base.num_bytes + dest_free.num_bytes
				
				result.absolute_offset = @dest.pos
				
				dest_base.write(@dest)
				dest_free.write(@dest)
			else
				raise "Invalid tag #{base.tag}"
			end
			
			result
		end
	end

end

def finish(msg)
	puts msg, "\nPress a key to close this application."
	STDIN.getch
	exit
end

input = ARGV.first

unless input
	begin
	  Win32::Registry::HKEY_CURRENT_USER.open('Software\GrindingGearGames\Path of Exile') do |reg|
		input = File.join(reg['InstallLocation'].to_s, 'Content.ggpk')
		input = nil unless File.exists?(input)
	  end
	rescue Win32::Registry::Error
	end
end

finish "No GGPK given and no Path of Exile installation detected. Please drag and drop the GGPK to defragment on this executable." unless input
finish "The given GGPK file '#{input}' doesn't exist" unless File.exists?(input)

puts "Defragmenting #{input}"

new = input + '.new'

begin
	fin = File.open(input, 'r+b')
rescue SystemCallError 
	finish "The GGPK appears to be in use. Please close Path of Exile."
end
old_size = fin.size
new_size = nil
time = Benchmark.realtime do
	begin
		File.open(new, 'w+b') do |fnew|
			fnew.seek 0
			GGPK.new(fin).defragment(fnew)
			new_size = fnew.size
		end
		fin.close
	rescue Exception
		File.delete(new)
		raise
	end

	File.delete(input)
	File.rename(new, input)
end

puts "Elapsed time: #{(time / 60.0).round(2)} minute(s)"
puts "File reduction: #{((old_size - new_size) / 1024.0 / 1024.0).round(2)} MB(s)"
finish "Successfully defragmented the GGPK."