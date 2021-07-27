cd include
clang++ -c -o FarosInstrument.o FarosInstrument.cpp
ar -crs libFarosInstrument.a FarosInstrument.o
