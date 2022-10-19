# 1、darknet计算mAP脚本：darknet_calc_mAP
# 2、images和xmls文件拆分脚本：train_val_split
# 3、cudahe cudnn版本读取
# 4、images_annotation_template, 用于整理xml标记图像后的处理。将all_images中已经标注了图像转移到images，同时输出一些信息。
# 5、training_custom_data_template，针对标记好的xml和对用images，来生成labels文件和images.txt路径。此外还可以，用于扩充images.txt文件。！！此文件需要手动创建文件夹。
# 6、修改xml文件的tag
# 7、数据集属性筛选xml和image。默认属性包括[person, head, helmet]，此文件用来筛选其中包含某个属性的xml和images，结果复制到filtered_images 和 filtered_annotations
# 8、opencv_video.py，opencv读取视频、分割成frame、保存视频等
