#include <stdlib.h>

int main(int argc, char *argv[])
{
  unsigned long long res = 0;
  for(unsigned int i = 0; i < 1024 * 1024; i++)
  {
    for(unsigned int y = 0; y < 1024 * 1024; y++)
    {
      res = (i + y) * 22;
    }
  }
  return EXIT_SUCCESS;
}