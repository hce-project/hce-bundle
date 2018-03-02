#include <stdlib.h>
#include <iostream>
#include <vector>

#define MB_DEFAULT 256
#define MB 1024 * 1024

int main(int argc, char *argv[])
{
  unsigned int mbCount = MB_DEFAULT;
  if(argc > 1)
  {
    mbCount = atoi(argv[1]);
  }
  std::vector<char> vec;
  char value = 33;
  for (unsigned int i = 0; i < mbCount; i++)
  {
    vec.insert(vec.begin(), MB, value);
  }
  std::cin >> mbCount;
  std::cout << vec.size() << std::endl;
  return EXIT_SUCCESS;
}