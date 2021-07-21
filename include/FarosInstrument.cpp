#include <iostream>
#include <chrono>
#include <fstream>




using std::cout; using std::endl;
using std::chrono::duration_cast;
using std::chrono::milliseconds;
using std::chrono::seconds;
using std::chrono::system_clock;
using namespace std;


void defaultInstrumentBegin(string outfile, string identifier){
    auto millisec_since_epoch = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    ofstream file;
  	file.open (outfile,ios::app);
  	file << identifier <<":Instrument Begin:"<<millisec_since_epoch<<"\n" ;
  	file.close();
    

}

void defaultInstrumentEnd(string outfile, string identifier){

	auto millisec_since_epoch = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    ofstream file;
  	file.open (outfile,ios::app);
  	file << identifier <<":Instrument End:"<<millisec_since_epoch<<"\n" ;
  	file.close();

}



