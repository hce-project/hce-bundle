#include <stdlib.h>
#include <fstream>

int main(int argc, char *argv[])
{
  std::fstream fs;
  fs.open("./test.txt", std::fstream::in | std::fstream::out | std::fstream::app);

  fs << " more lorem ipsum";
  for(unsigned int y = 0; y < 1024 * 1024; y++)
  {
    for (unsigned int i = 0; i < 1024 * 1024; i++)
    {
      fs << "AA  ";
    }
  }
  fs.close();
  return EXIT_SUCCESS;
}