#!/usr/bin/env ruby
require 'open-uri'

num_threads = 30
threads = []

contentsArray = File.readlines('/tmp/alluris.txt')
size = contentsArray.length / num_threads
contents = contentsArray.each_slice(size).to_a
puts contents.length
puts contents[0][0]

size.times do |j|
  num_threads.times do |i|
    threads[i] = Thread.new do
      begin
        puts "#{i} #{j} "
        puts "#{i} #{j} #{contents[i][j]}"
        kittens = open(contents[i][j],http_basic_authentication: ["admin", "admin"])
        response_body = kittens.read

        #puts response_body
      rescue Exception => e
        puts e.message
      end
    end
  end
end
threads.each { |thread| thread.join }
