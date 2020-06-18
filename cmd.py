import mugenrivals
import sys

if len(sys.argv) < 2:
	input("Enter a folder as an argument")
else:
    mugenrivals.main(sys.argv[1])