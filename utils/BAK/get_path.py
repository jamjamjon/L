import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', type=str, required=True)
    parser.add_argument('--append', action='store_true',help='append to exist file or rewrite')
    parser.add_argument('--save-txt', default="save_out.txt",type=str, required=True)


    args = parser.parse_args()
    

    image_dir = os.path.abspath(args.d)

    

    if args.append:
        f = open(args.save_txt, 'a')
    else:
        f = open(args.save_txt, 'w')


    images_list = [x for x in os.listdir(image_dir) if not x.endswith(".txt")]
    print(f"==>image num: {len(images_list)}")

    for item in images_list:
        image_path = os.path.join(image_dir, item)
        f.write(image_path + '\n')


    f.close()
