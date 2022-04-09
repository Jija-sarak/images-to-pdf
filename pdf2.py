from pathlib import Path
from PIL import Image
import pdf2image
import glob
import os

def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst


def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst


def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)

# Converting pdf to images
def image_conversion(inpath,image_path):
  print("converting to image")
  OUTPUT_FOLDER = None
  FIRST_PAGE = 1
  LAST_PAGE = 16
  FORMAT = 'jpg'
  USERPWD = None
  USE_CROPBOX = False
  STRICT = False

  Name = Path(inpath).stem
  pil_images = pdf2image.convert_from_path(inpath,
                                          output_folder = OUTPUT_FOLDER,
                                          first_page = FIRST_PAGE,
                                          last_page = LAST_PAGE,
                                          fmt = FORMAT,
                                          userpw = USERPWD,
                                          use_cropbox= USE_CROPBOX,
                                          strict = STRICT)

  list1 = []
  list2 = []
  i = 1
  for image in pil_images :
        image.save(image_path+"/"+Name+str(i)+".jpg")
        if i%2==0:
            img = Image.open(image_path+"/"+Name+str(i)+".jpg")
            list2.append(img)
        else :
            img = Image.open(image_path+"/"+Name+str(i)+".jpg")
            list1.append(img)
        i+=1

  get_concat_tile_resize([[list2[-1],list1[0]],
                          [list2[-2],list1[1]],
                          [list2[-3],list1[2]],
                          [list2[-4],list1[3]]]).save(image_path+'/'+Name+'1.png')
  get_concat_tile_resize([[list2[0],list1[-1]],
                          [list2[1],list1[-2]],
                          [list2[2],list1[-3]],
                          [list2[3],list1[-4]]]).save(image_path+'/'+Name+'2.png')

  # Incerting 2 images to one pdf
  def imgToPDF():
        image_1 = Image.open(image_path+'/'+Name+'1.png')
        image_2 = Image.open(image_path+'/'+Name+'2.png')


        im_1 = image_1.convert('RGB')
        im_2 = image_2.convert('RGB')


        image_list = [im_2]

        im_1.save(image_path+'/'+Name+'2.pdf', save_all=True, append_images=image_list)
        # removing all images from the file
        for path in Path(image_path).iterdir() :
            path_all = glob.glob (str(path))
            extension=('pdf') # ('edf','json','Dat','Plb','docx','txt') _if to keep more than one extension type
            path_remove=[filename for filename in path_all if not filename.endswith ( extension )]
            [os.remove ( filePath ) for filePath in path_remove]
  imgToPDF()

inpath = input("Enter a pdf file path :- ") # Give a pdf file path which you want to convert into image
image_path = input("Enter a output image path :- ") # Give a output folder path where you want to store the output image
image_conversion(inpath , image_path)