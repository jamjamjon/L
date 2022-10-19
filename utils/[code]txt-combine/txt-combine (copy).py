from pathlib import Path
import shutil
import os
from tqdm import tqdm
import argparse
import rich





# ----------------options ------------------------
def parse_opt():
	parser = argparse.ArgumentParser(description='Open-source image labeling tool')

	# basic directory
	parser.add_argument('--A', default='', type=str, help='Path to input directory')
	parser.add_argument('--B', default='', type=str, help='Path to input directory')
	parser.add_argument('--output', default='output', type=str, help='Path to output directory')


	opt = parser.parse_args()
	rich.print(f"[bold]{opt}\n")
	return opt



def main(opt):

	## saveout dir
	if not Path(opt.output).exists():
		Path(opt.output).mkdir()
	else:
		rich.print("output dir exist!")
		# exit(-1)


	# list txt file A B 
	A_list = [x for x in Path(opt.A).iterdir() if x.suffix == ".txt"]
	B_list = [x for x in Path(opt.B).iterdir() if x.suffix == ".txt"]

	rich.print(f"num_list_A: {len(A_list)}")
	rich.print(f"num_list_B: {len(B_list)}")


	# loop A
	for a in tqdm(A_list):

		if Path(opt.B) / a.name not in B_list:
			shutil.copy(str(a), str(Path(opt.output)))
		else:
			saveout = Path(opt.output) / a.name
			with open(saveout, "a") as f_output:

				# read a
				f_A = open(a, "r").read()
				# print(f"A:\n{f_A}")

				# read b
				f_B = open(Path(opt.B) / a.name, "r").read()
				# print(f"B:\n{f_B}")

				# write to output
				f_output.write(f_A + f_B)


	# loop B
	for b in tqdm(B_list):
		if Path(opt.A) / b.name not in A_list:
			shutil.copy(str(b), str(Path(opt.output)))
		else:
			continue


	# output dir info
	output_list = [x for x in Path(opt.output).iterdir() if x.suffix == ".txt"]
	rich.print(f"num_output_dir: {len(output_list)}")


# ---------------------------------------------------
#   main
#--------------------------------------------------
if __name__ == '__main__':
	# options
	opt = parse_opt()
	main(opt)



















