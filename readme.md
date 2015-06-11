# Project UTL Indexer

## The Problem

With Townnews emphasizing the use of macros/components with its UTL template language ([Townnews Documentation][]), it is becoming increasingly necessary to look up definitions in another file to understand what is being done. However, the current tools in Townnews' development environment make this quite difficult: one can search on a macro name, but all you get are a list of files with a count of the occurences of the name, and no way to distinguish a defining file from a using file.

## The Vision

The eventual goal for this project is a web page where you type in the name of a macro, and it tells you the file and line for the macro definition. Ideally it would also display the text the macro.

[Townnews Documentation]: http://docs.townnews.com/kbpublisher/722/
