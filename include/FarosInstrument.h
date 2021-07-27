#include <iostream>
using namespace std;

void defaultInstrumentBegin(string outfile, string identifier);
void defaultInstrumentEnd(string outfile, string identifier);
void lazyWrite(long currentTime, std::string message, std::string outfile);
