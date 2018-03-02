#! /bin/bash
#
#

# escape sequences
red='\e[0;31m'
nc='\e[0m'

# print string in red
function say() {
  echo -ne "${red}$*"
  echo -ne "${nc}"
}
