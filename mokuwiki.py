#!/usr/bin/env python

""" mokuwiki.py

Converts a folder of Markdown files, applying the following transforms:

*  Inter-page links can be specified using the target page's title (as specified in its YAML
metadata block), e.g. '[[A Page Title]]'. This is converted to a standard Markdown link to the
HTML version of that page: '[A Page Title](a_page_title.html)'.

*  The YAML metadata can also have an "alias" field which can be used to link to that page instead
of the title. This can be useful if the actual title that is to be displayed (the "formal" title,
if you will) is long but has a common shorter form. Aliases must be unique and not the same as any
title.

*  Tags can also be specified in the YAML metadata block. They can be referenced in a page using
the following syntax: '{{tag1}}'. This will produce a list of page links that have the "tag1" tag.
Lists of pages can be created by combining tags in various ways:
	*  {{tag1 tag2}} lists all pages with 'tag1' or 'tag2'
	*  {{tag1 +tag2}} lists all pages with 'tag1' and 'tag2'
	*  {{tag1 -tag2}} lists all pages with 'tag1' that do not have 'tag2'
	*  {{*}} list all pages that have any tag at all
	*  {{#}} the total number of pages
	*  {{#tag}} the total number of pages with 'tag'
	*  {{@}} a list of all tags (bracketed spans with a class of 'tag')

*  Files can be included in other files using the following syntax: '<<include_me.md>>'. Multiple
file specifications are also supported, e.g. '<<include*X.dat>>'. YAML metadata blocks are removed
on inclusion and separator text can be defined to be inserted after each file (except the last) by
using the '--separator' command line argument.

*  Image links can be inserted with the following syntax: '!!Image Name!!'. This will produce an
image link like: '![Image Name](images/image_name.jpg)', that is, the file name is based on the
caption. Images are assumed to live in a local "images" folder but this can be changed with the
'--media' command line option. They are also assumed to be JPGs.

The files in the specified output folder are named according to their title (not their input file
name). For example, a page called "file1.md" with the "title" metadata equal to "A Page Title" will
be converted to "a_page_title.md". Output files can then be processed using a Markdown processor
(the assumption is that pandoc is being used).

Using the '--index' option will also output a "_index.json" file that contains a JSON object
suitable for use by a search function in a webpage.

"""

import os
import re
import json
import glob
import string
import argparse

###

def process_files(source, target, index=False, list=False, fullns=False, broken="broken", tag="tag", media="images", separator=""):

	# configure
	config.source = source
	config.target = target
	config.index = index
	config.list = list
	config.fullns = fullns
	config.broken = broken
	config.tag = tag
	config.media = media
	config.separator = separator

	# get list of Markdown files
	file_list = glob.glob(config.source + "/*.md")

	# create indexes
	create_indexes(file_list)

	# process files
	for file in file_list:

		with open(file, "r") as input_file:
			contents = input_file.read()

		title = parse_metadata("title", contents)

		if not title:
			print "mokuwiki: skipping '" + file + "', no title found"
			continue

		# replace file transclusion first (may include tag and page links)
		contents = regex_link["file"].sub(convert_file_link, contents)

		# replace tag links next (this may create page links, so do this before page links)
		contents = regex_link["tags"].sub(convert_tags_link, contents)

		# replace page links
		contents = regex_link["page"].sub(convert_page_link, contents)

		# replace image links
		contents = regex_link["image"].sub(convert_image_link, contents)

		# get output file name by adding ".md" to title's file name
		with open(os.path.join(config.target, page_index["title"][title] + ".md"), "w") as output_file:
			output_file.write(contents)

		# add terms to search index
		if config.index:
			update_search_index(contents, title)

	# show list of broken links

	if config.list:
		print '\n'.join(sorted(page_index["broken"]))

	# write search index

	if config.index:
		search_index = "var MW = MW || {};\nMW.searchIndex = " + json.dumps(page_index["search"], indent=4)

		with open(os.path.join(config.target, "_index.json"), "w") as json_file:
			json_file.write(search_index)


###

def create_indexes(file_list):
	# create all indexes

	for file in file_list:

		with open(file, "r") as input_file:
			contents = input_file.read()

		# get title
		title = parse_metadata("title", contents)

		if not title:
			continue

		if title not in page_index["title"]:
			page_index["title"][title] = create_valid_filename(title)
		else:
			print "mokuwiki: skipping '" + file + "', duplicate title '" + title + "'"
			continue

		# get alias (if any)
		alias = parse_metadata("alias", contents)

		if alias:
			if alias not in page_index["alias"] and alias not in page_index["title"]:
				page_index["alias"][alias] = title
			else:
				print "mokuwiki: duplicate alias '" + alias + "' in file '" + file + "'"

		# get list of tags (if any)
		tags = parse_metadata("tags", contents)

		if not tags:
			continue

		# add each tag to index, with titles as set
		for tag in tags:

			# strip end spaces and convert to lower case
			tag_name = tag.strip().lower()

			if tag_name not in page_index["tags"]:
				page_index["tags"][tag_name] = set()

			page_index["tags"][tag_name].add(title)


###

def update_search_index(contents, title):
	# update the search index with strings extracted from metadata

	# at this point must have a title
	terms = parse_metadata("title", contents)

	alias = parse_metadata("alias", contents)

	if alias:
		terms += " " + alias

	summary = parse_metadata("summary", contents)

	if summary:
		terms += " " + summary

	tags = parse_metadata("tags", contents)

	if tags:
		# convert tags list to string
		terms += " " + " ".join(tags)

	keywords = parse_metadata("keywords", contents)

	if keywords:
		# convert keywords list to string
		terms += " " + " ".join(keywords)

	# remove punctuation etc from YAML values, make lower case, remove commas (e.g. from numbers in summary)
	table = string.maketrans(";_()", "    ")
	terms = terms.translate(table).replace(",","").lower().split()

	# remove stop words
	terms = [word for word in terms if word not in stop_list]

	# update search index, use unique terms only (set() removes duplicates)
	search = { "file" : page_index["title"][title],
			   "title" : title,
			   "terms" : ' '.join(str(s) for s in set(terms)) }

	page_index["search"].append(search)


###

def convert_page_link(page):
	# return a page link constructed from the given page title

	# usual format is [[Page name]] or [[Show name|Page name]]
	# with namespaces format is [[ns:Page name]] or [[Show name|ns:Page name]]

	page_name = str(page.group())[2:-2]
	show_name = ""

	if "|" in page_name:
		show_name, page_name = page_name.split("|")

	# resolve namespace
	namespace = ""

	if ":" in page_name:
		namespace, page_name = page_name.rsplit(":", 1)

		namespace = namespace.replace(":","/") + "/"

		if not config.fullns:
			namespace = "../" + namespace

	# set show name if not already done
	if not show_name:
		show_name = page_name

	# resolve any alias for the title
	if page_name in page_index["alias"]:
		page_name = page_index["alias"][page_name]

	page_link = ""

	if page_name in page_index["title"]:
		# if title exists in index make into a link
		page_link = "[" + show_name + "](" + page_index["title"][page_name] + ".html)"

	else:
		if namespace:
			# title not in index but namespace set, make up link on the fly
			page_link = "[" + show_name + "](" + namespace + create_valid_filename(page_name) + ".html)"
		else:
			# if title does not exist in index then turn into bracketed span with class='broken' (default)
			page_link = "[" + page_name + "]{." + config.broken + "}"

			page_index["broken"].add(page_name)

	return page_link


###

def convert_tags_link(tags):
	# return a string containing a list of page links derived from a tag specification

	tag_list = str(tags.group())[2:-2]
	tag_list = tag_list.split()

	# get initial category
	tag_name = tag_list[0].replace("_"," ").lower()
	tag_links = ""

	# check that first tag value exists
	if tag_name not in page_index["tags"]:

		# check for special characters
		if "*" in tag_name:
			# if the first tag contains a "*" then list all pages
			tag_links = "[[" + "]]\n\n[[".join(sorted(page_index["title"].keys())) + "]]\n\n"

		elif "@" in tag_name:
			# if the first tag contains a "@" then list all tags as bracketed span with class='tag' (default)
			tag_class = "]{." + config.tag + "}\n\n["
			tag_links = "[" + tag_class.join(sorted(page_index["tags"].keys())) + "]{." + config.tag + "}"

		elif "#" in tag_name:
			# if the first tag contains a "#" then return the count of pages

			if tag_name == "#":
				# a single "#" returns total number of pages
				tag_links = str(len(page_index["title"].keys()))
			else:
				# the string "#tag" returns number of pages with that tag
				if tag_name[1:] in page_index["tags"]:
					tag_links = str(len(page_index["tags"][tag_name[1:]]))

	else:
		# copy first tag set
		page_set = set(page_index["tags"][tag_name])

		# add other categories
		for __, tag in enumerate(tag_list[1:]):

			if tag[0] == '+' or tag[0] == '-':
				tag_name = tag[1:]
			else:
				tag_name = tag

			# normalise tag name
			tag_name = tag_name.replace("_"," ").lower()

			if tag_name not in page_index["tags"]:
				continue

			if tag[0] == '+':
				page_set &= page_index["tags"][tag_name]
			elif tag[0] == '-':
				page_set -= page_index["tags"][tag_name]
			else:
				page_set |= page_index["tags"][tag_name]

		# format the set into a string of page links, sorted alphabetically
		tag_links = "[[" + "]]\n\n[[".join(sorted(page_set)) + "]]\n\n"

	# return list of tag links
	return tag_links


###

def convert_file_link(file):
	# insert contents of file

	incl_list = str(file.group())[2:-2]

	incl_list = sorted(glob.glob(config.source + "/" + incl_list))

	incl_contents = ""

	for i, file in enumerate(incl_list):

		with open(file, "r") as incl_file:
			file_contents = incl_file.read()

		# remove any YAML block
		file_contents = regex_meta["yaml"].sub("", file_contents)

		if i < len(incl_list) - 1:
			file_contents += "\n\n" + config.separator

		incl_contents += file_contents + "\n\n"

	# return contents of all matched files
	return incl_contents


###

def convert_image_link(image):
	# return a string containing an image link

	image_name = str(image.group())[2:-2]

	image_link = "![" + image_name + "](" + config.media + "/" + create_valid_filename(image_name) + ".jpg)"

	return image_link


###

def create_valid_filename(name):
	# return a valid filename from the given name

	# see also https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename and Django comment about removing unicode chars
	name = str(name).strip().replace(' ', '_').lower()
	return re.sub(r'(?u)[^-\w.]', '', name)


###

def parse_metadata(metadata, contents):
	# return the contents for the given metadata string, using the global regex's
	# return type is string for simple fields, list for lists

	if metadata not in regex_meta:
		return None

	value = regex_meta[metadata].search(contents)

	if not value:
		return None

	# get raw string value
	value = value.group(1).strip()

	# convert to list if required
	if value.startswith("[") and value.endswith("]"):
		value = value[1:-1].split(",")

	return value


### MAIN ###

# regular expressions to locate YAML metadata

regex_meta = {}
regex_meta["title"] = re.compile(r"[T|t]itle:(.*)[\r\n|\r|\n]")
regex_meta["alias"] = re.compile(r"[A|a]lias:(.*)[\r\n|\r|\n]")
regex_meta["tags"] = re.compile(r"[T|t]ags:(.*)[\r\n|\r|\n]")
regex_meta["keywords"] = re.compile(r"[K|k]eywords:(.*)[\r\n|\r|\n]")
regex_meta["summary"] = re.compile(r"[S|s]ummary:(.*)[\r\n|\r|\n]")
regex_meta["yaml"] = re.compile(r"---[\r\n|\r|\n].*[\r\n|\r|\n]\.\.\.", re.DOTALL)

# regular expressions to locate page, tag, file and image links

regex_link = {}
regex_link["page"] = re.compile(r"\[\[[\w\s,.:|'-]*\]\]")
regex_link["tags"] = re.compile(r"\{\{[\w\s\*#@'+-]*\}\}")
regex_link["file"] = re.compile(r"<<[\w.*?-]*>>")
regex_link["image"] = re.compile(r"!![\w\s,.:|'-]*!!")

# set up indexes

page_index = {}
page_index["tags"] = {}			# index of tags, containing set of titles with that tag
page_index["title"] = {}		# index of titles, containing associated base file name
page_index["alias"] = {}		# index of title aliases (one per page only, must be unique and not in a title)
page_index["search"] = []		# index of search terms (for JSON search index)
page_index["broken"] = set()	# index of broken links (page names that are not in index)

# list of stop words for search indexing

stop_list = ['a', 'an', 'and', 'be', 'but', 'by', 'i', 'it', 'is', 'of', 'on', 'the']

# configuration object

class Config(object):
	pass

config = Config()

# set defaults

config.index = False
config.list = False
config.fullns = False
config.broken = "broken"
config.tag = "tag"
config.media = "images"
config.separator = ""

# execute if main

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Convert folder of Markdown files to support interpage linking and tags")
	parser.add_argument("source", help="Source directory")
	parser.add_argument("target", help="Target directory")
	parser.add_argument("-i", "--index", help="Produce JSON search index", action="store_true")
	parser.add_argument("-l", "--list", help="List broken links", action="store_true")
	parser.add_argument("-f", "--fullns", help="Use full paths for namespaces", action="store_true")
	parser.add_argument("-b", "--broken", default="broken", help="CSS class for broken links (default is 'broken')")
	parser.add_argument("-t", "--tag", default="tag", help="CSS class for tag links (default is 'tag')")
	parser.add_argument("-m", "--media", default="images", help="Path to media files (default is 'images')")
	parser.add_argument("-s", "--separator", default="", help="Separator to insert between transcluded files (default is empty)")
	parser.parse_args(namespace=config)

	process_files(config.source, config.target,
				  index=config.index, list=config.list, fullns=config.fullns, broken=config.broken,
				  tag=config.tag, media=config.media, separator=config.separator)
