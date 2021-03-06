# Project UTL Indexer

## The Problem

With Townnews emphasizing the use of macros/components with its UTL template language ([Townnews Documentation][]), it is becoming increasingly necessary to look up definitions in another file to understand what is being done. This involves a tedious text search across all the template files for a site.

## The Vision

The eventual goal for this project is a web page where you type in the name of a macro, and it tells you the file and line for the macro definition. Ideally it would also display the text of the macro.

## The Tools

The lexical analysis and parsing is done with [Python (version 3)][] scripts, using a third-party library called [ply][]. Basically, ply is a port to Python of the standard UNIX tools lex and grep.

Currently the lexical analysis and parse is done from reverse-engineering the UTL scripts, and what documentation Townnews has provided. It would be helpful to have a standard [BNF][] definition for the syntax; on the other hand, defining it from examples is proving very educational.

[Townnews Documentation]: http://docs.townnews.com/kbpublisher/722/
[Python (version 3)]: https://docs.python.org/3/
[BNF]: http://en.wikipedia.org/wiki/Backus%E2%80%93Naur_Form
[ply]: http://www.dabeaz.com/ply/

## Known Problems

The parser can handle a trailing comma in an array literal [example: `[1, 2, 3,]`] but not some situations that are legal according to Townnews' parser (`[,]`, `[1,2,3,,]`).
