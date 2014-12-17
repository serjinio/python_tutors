
#include <stdlib.h>
#include <stdio.h>
#include <math.h>


// constants for calcution of frequencies for
// p-terphenyl host crystal
double const X_PTERPH = 518.54;
double const Y_PTERPH = 411.84;
double const Z_PTERPH = -930.38;
double const B_PTERPH = 1.399;
double const G_PTERPH = 2.0;

double const X_NAPH = 503.0;
double const Y_NAPH = 418.0;
double const Z_NAPH = -921.0;
double const B_NAPH = 1.399;
double const G_NAPH = 2.0;


int main()
{
  int esri;
  double esr;

  double x = X_NAPH;
  double y = Y_NAPH;
  double z = Z_NAPH;
  double b = B_NAPH;
  double g = G_NAPH;

  double nmr = 0.00426043;

  double hu,hl;
  double hu1,hu2,hl1,hl2;


  for(esri=0; esri<15000; esri++){
    esr=esri*1.0;

    hu1 = sqrt(-((esr+x-(y+z)/2.)*(esr+x-(y+z)/2.) - (y-z)*(y-z)/4)/g/g/b/b);
    hl1 = sqrt(-((esr-x+(y+z)/2.)*(esr-x+(y+z)/2.) - (y-z)*(y-z)/4)/g/g/b/b);

    hu2 = sqrt(((esr+x-(y+z)/2.)*(esr+x-(y+z)/2.) - (y-z)*(y-z)/4)/g/g/b/b);
    hl2 = sqrt(((esr-x+(y+z)/2.)*(esr-x+(y+z)/2.) - (y-z)*(y-z)/4)/g/g/b/b);

    if(hu1 > 0.0) hu=hu1;
    else if(hu2 > 0.0) hu=hu2;

    if(hl1 > 0.0) hl=hl1;
    else if(hl2 > 0.0) hl=hl2;

    printf("%10.1lf %10.6lf %10.3lf %10.6lf %10.3lf\n", esr, hl * nmr,
	   hl * nmr * 2.0 * 3.14159 / 2.67513 * 10.0, hu * nmr,
	   hu * nmr * 2.0 * 3.14159 / 2.67513 * 10.0);
  }

  exit(0);
}
