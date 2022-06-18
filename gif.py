import sys, os.path, traceback


def make_gif_data(image_height, image_width, global_color_table, index_stream):
    with open("gif_data.js", "w") as f:
        gif_data = f"let {image_height = };\n"
        gif_data += f"let {image_width = };\n"
        gif_data += f"let {global_color_table = };\n"
        gif_data += f"let {index_stream = };\n"
        f.write(gif_data)


def gif(f_path, r_html=None):
    buf = None
    temp_var = None

    #header
    gif_header = None
    gif_version = None

    #logical screen descriptor
    logical_screen_height = None
    logical_screen_width = None
    global_color_table_flag = None
    color_resolution = None
    global_sort_flag = None
    size_of_global_table = None
    background_color_index = None
    pixel_aspect_ratio = None

    #global color table
    global_color_table = []

    #application extension

    #graphic control extension

    #comment extension
    comment_data = None

    #image descriptor
    image_left_pos = None
    image_top_pos = None
    image_width = None
    image_height = None
    local_color_table_flag = None
    interlace_flag = None
    sort_flag = None
    size_of_local_table = None

    #local color table
    local_color_table = []

    #image data
    lzw_minimal_code_size = None
    code_size = None
    sub_block = None
    sub_block_size = None
    code_table = {}
    code_stream = []
    index_stream = []
    

    with open(f_path, "rb") as fab:
        #header
        buf = fab.read(6).decode("ascii")
        if (buf == "GIF87a" or buf == "GIF89a"):
            gif_header = buf
            gif_version = buf[3:]
        else:
            sys.exit("this file is not a gif")


        #logical screen descriptor
        logical_screen_width = int.from_bytes(fab.read(2), byteorder="little")
        logical_screen_height = int.from_bytes(fab.read(2), byteorder="little")
        
        buf = bin(fab.read(1)[0])[2:].zfill(8)
        global_color_table_flag = bool(int(buf[0]))

        # in 89a spec - 1
        color_resolution = int(buf[1:4], 2) + 1

        # reserved in 87a and should be 0
        global_sort_flag = bool(int(buf[4]))

        size_of_global_table = int(buf[5:], 2)
        background_color_index = fab.read(1)[0]
        pixel_aspect_ratio = fab.read(1)[0]


        #global color table
        if(global_color_table_flag):
            for n in range(2 ** (size_of_global_table + 1)):
                temp_var = []
                for i in range(3):
                    temp_var.append(fab.read(1)[0])
                global_color_table.append(temp_var)


        #extensions not have correct order so parce everything that can be found before moving on
        buf = fab.read(1)[0]
        while buf != 0x2C:
            #application extension
            #TODO
            if(buf == 0x21):
                if(fab.read(1)[0] != 0xFF):
                    fab.seek(-1, 1)
                else:
                    if(fab.read(1)[0] != 0x0B):
                        sys.exit("block size in application extension is not 0x0B")
                    else:
                        fab.seek(11, 1)
                        buf = fab.read(1)[0]
                        fab.seek(buf, 1)
                        if(fab.read(1)[0] != 0x00):
                            sys.exit("block terminator in application extension not found")
                        else:
                            buf = fab.read(1)[0]
            
            #comment extension
            if(buf == 0x21):
                if(fab.read(1)[0] != 0xFE):
                    fab.seek(-1, 1)
                else:
                    comment_data = ""
                    buf = fab.read(1)
                    while buf[0] != 0x00:
                        comment_data += buf.decode("ascii")
                        buf = fab.read(1)
                    print(f"{comment_data=}")
                    buf = fab.read(1)[0]

            #graphic control extension
            #TODO
            if(buf == 0x21):
                if(fab.read(1)[0] != 0xF9):
                    fab.seek(-1, 1)
                else:
                    fab.seek(5, 1)
                    if(fab.read(1)[0] != 0x00):
                        sys.exit("block terminator in graphic control extension not found")
                    else:
                        buf = fab.read(1)[0]

        #image descriptor
        if(buf != 0x2C):
            sys.exit("image separator is not 0x2C")

        image_left_position = int.from_bytes(fab.read(2), byteorder="little")
        image_top_position = int.from_bytes(fab.read(2), byteorder="little")

        image_width = int.from_bytes(fab.read(2), byteorder="little")
        if(image_width > logical_screen_width):
            sys.exit("image_width bigger than logical_screen_width")

        image_height = int.from_bytes(fab.read(2), byteorder="little")
        if(image_height > logical_screen_height):
            sys.exit("image_height bigger than logical_screen_height")

        buf = bin(fab.read(1)[0])[2:].zfill(8)

        local_color_table_flag = bool(int(buf[0]))
        interlace_flag = bool(int(buf[1]))
        sort_flag = bool(int(buf[2]))
        size_of_local_table = int(buf[5:], 2)

        #local color table
        #TODO currently local_color_table overwrite global_color_talbe
        if(local_color_table_flag):
            global_color_table = []
            for n in range(2 ** (size_of_local_table + 1)):
                temp_var = []
                for i in range(3):
                    temp_var.append(fab.read(1)[0])
                global_color_table.append(temp_var)


        #image data
        lzw_minimal_code_size = fab.read(1)[0]
        code_size = lzw_minimal_code_size
        if(code_size > 12):
            code_size = 12

        sub_block_size = fab.read(1)[0]

        for i in range(len(global_color_table)):
            code_table[i] = [i]

        code_table[len(code_table)] = "CLR"
        code_table[len(code_table)] = "EOI"

        CLR_pos = len(code_table) - 2
        EOI_pos = len(code_table) - 1

        init_code_table = code_table.copy()

        if(len(code_table) > ((2 ** code_size))):
            code_size += 1

        init_code_size = code_size
        
        buf = []
        while True:
            sub_block = fab.read(sub_block_size)
            for i in range(len(sub_block)):
                buf.append(bin(int(sub_block[i]))[2:].zfill(8))

            sub_block_size = fab.read(1)[0]
            if(sub_block_size == 0):
                break

        sub_block = None
        buf.reverse()
        #TODO join strings via join() or (buf = bin(int(sub_block[i]))[2:].zfill(8) + buf) is slow for some reason
        # so we need decode image by using sub block one by one, not a whole image data in buf
        buf = "".join(buf)

        try:
            current_code = int(buf[-code_size:], 2)
            buf = buf[:-code_size]
            if(current_code == CLR_pos):
                code_stream.append(current_code)

                current_code = int(buf[-code_size:], 2)
                buf = buf[:-code_size]
                code_stream.append(current_code)
                index_stream.append(current_code)

                prev_code = current_code

                if(len(code_table) == ((2 ** code_size) - 1)):
                    if (code_size < 12):
                        code_size += 1

                while (len(buf) > 0):
                    current_code = int(buf[-code_size:], 2)
                    buf = buf[:-code_size]
                    code_stream.append(current_code)

                    # only works in this position and i dont know why
                    if(len(code_table) == ((2 ** code_size) - 1)):
                        if (code_size < 12):
                            code_size += 1

                    if(current_code == EOI_pos):
                        break

                    if(current_code == CLR_pos):
                        code_size = init_code_size
                        code_table = init_code_table.copy()

                        code_stream.append(current_code)

                        current_code = int(buf[-code_size:], 2)
                        buf = buf[:-code_size]
                        code_stream.append(current_code)
                        index_stream.append(current_code)

                        prev_code = current_code
                        continue
                    
                    if(current_code in code_table):
                        index_stream.append(code_table[current_code])
                        code_table[len(code_table)] = code_table[prev_code].copy()
                        code_table[len(code_table) - 1].append(code_table[current_code][0])
                        prev_code = current_code
                    else:
                        index_stream.append(code_table[prev_code].copy())
                        index_stream[-1].append(code_table[prev_code][0])
                        code_table[len(code_table)] = code_table[prev_code].copy()
                        code_table[len(code_table) - 1].append(code_table[prev_code][0])
                        prev_code = current_code
        except Exception:
            print(len(code_table), current_code, prev_code)
            traceback.print_exc()

    if (r_html):
        make_gif_data(image_height, image_width, global_color_table, index_stream)

def main():
    print(sys.argv)
    
    """
    r_html = False
    if(len(sys.argv) == 3):
        if(sys.argv[1] == "-r"):
            r_html = True

        f = sys.argv[2]
        if (os.path.isfile(f)):
            gif(f, r_html)
        else:
            sys.exit("given path is not a file")
    """
    
    if(len(sys.argv) == 2):
        f = sys.argv[1]
        if (os.path.isfile(f)):
            gif(f, True)
        else:
            sys.exit("given path is not a file")


if (__name__ == "__main__"):
    main()