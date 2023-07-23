import sys
import os

def gif(f_path, export_gif_data = None):
    # header
    gif_header = None

    # logical screen descriptor
    logical_screen_height = None
    logical_screen_width = None
    global_color_table_flag = None
    color_resolution = None
    global_sort_flag = None
    size_of_global_table = None
    background_color_index = None
    pixel_aspect_ratio = None

    # global color table
    global_color_table = []

    # graphic control extension
    disposal_method = None
    user_input_flag = None
    transparent_color_flag = None
    delay_time = None
    transparent_color_index = None

    # comment extension
    comment_data = None

    # plain text extension
    text_grid_left_pos = None
    text_grid_top_pos = None
    text_grid_width = None
    text_grid_height = None
    char_cell_width = None
    char_cell_height = None
    text_foreground_color_index = None
    text_background_color_index = None
    plain_text_data = None

    # application extension
    application_identifier = None
    application_identifier_code = None
    application_data = None

    # image descriptor
    image_left_pos = None
    image_top_pos = None
    image_width = None
    image_height = None
    local_color_table_flag = None
    interlace_flag = None
    sort_flag = None
    size_of_local_table = None

    # local color table
    local_color_table = []

    # image data
    lzw_minimal_code_size = None
    code_size = None
    sub_block = None
    sub_block_size = None
    code_table = {}
    code_stream = []
    index_stream = []

    # etc
    frames = 0
    local_color_table_flags = []
    local_color_tables = []

    with open(f_path, "rb") as fab:
        # header
        gif_header = fab.read(6).decode("ascii", errors="ignore")
        if (gif_header not in ["GIF87a", "GIF89a"]):
            sys.exit("this file is not a gif")


        # logical screen descriptor
        logical_screen_width = int.from_bytes(fab.read(2), byteorder="little")
        logical_screen_height = int.from_bytes(fab.read(2), byteorder="little")

        buf = bin(int.from_bytes(fab.read(1), byteorder="little"))[2:].zfill(8)

        global_color_table_flag = bool(int(buf[0]))
        color_resolution = int(buf[1:4], 2) - 1
        global_sort_flag = bool(int(buf[4])) # reserved in 87a and should be 0
        size_of_global_table = int(buf[5:], 2)

        background_color_index = int.from_bytes(fab.read(1), byteorder="little")
        pixel_aspect_ratio = int.from_bytes(fab.read(1), byteorder="little")


        # global color table
        if (global_color_table_flag):
            for i in range((2 ** (size_of_global_table + 1)) * 3):
                global_color_table.append(int.from_bytes(fab.read(1), byteorder="little"))


        buf = fab.read(1)
        while buf != b"\x3B":
            # skip extentions
            while buf != b"\x00":
                if (buf == b"\x21"):
                    print("skip extention:", fab.read(1))
                    while buf != 0:
                        buf = int.from_bytes(fab.read(1), byteorder="little")
                        fab.seek(buf, 1)
                    buf = fab.read(1)
                else:
                    break

            """
            #extensions not have correct order so parse everything that can be found before moving on
            buf = fab.read(1)[0]
            while buf == 0x21:
                #graphic control extension
                if(fab.read(1)[0] != 0xF9):
                    fab.seek(-1, 1)
                else:
                    buf = fab.read(1)[0]
                    if(buf != 4):
                        sys.exit("block size in graphic control extension is not 4")
                    buf = fab.read(buf)
                    if(len(buf) != 4):
                        sys.exit("size of graphic control extension is not 4")

                    another_buf = bin(buf[:1][0])[2:].zfill(8)
                    buf = buf[1:]

                    disposal_method = int(another_buf[3:6])
                    user_input_flag = bool(int(another_buf[6]))
                    transparent_color_flag = bool(int(another_buf[7]))

                    delay_time = int.from_bytes(buf[:2], byteorder="little")
                    buf = buf[2:]

                    transparent_color_index = int(buf[:1][0])

                    if(fab.read(1)[0] != 0x00):
                        sys.exit("block terminator in graphic control extension not found")
                    
                    buf = fab.read(1)[0]

                #comment extension
                if(fab.read(1)[0] != 0xFE):
                    fab.seek(-1, 1)
                else:
                    comment_data = ""
                    sub_block_size = fab.read(1)[0]
                    while True:
                        comment_data += fab.read(sub_block_size).decode("ascii")

                        sub_block_size = fab.read(1)[0]
                        if(sub_block_size == 0):
                            break
                    
                    print("comment_data:\n" + comment_data)

                    buf = fab.read(1)[0]

                #plain text extension
                #TODO seems this block placed after image data and can work as image data (using delay time and render text on top past frame)
                if(fab.read(1)[0] != 0x01):
                    fab.seek(-1, 1)
                else:
                    buf = fab.read(1)[0]
                    if(buf != 12):
                        sys.exit("block size in plain text extension is not 12")
                    buf = fab.read(buf)
                    if(len(buf) != 12):
                        sys.exit("size of plain text extension is not 12")
                    
                    text_grid_left_pos = int.from_bytes(buf[:2], byteorder="little")
                    buf = buf[2:]
                    text_grid_top_pos = int.from_bytes(buf[:2], byteorder="little")
                    buf = buf[2:]

                    text_grid_width = int.from_bytes(buf[:2], byteorder="little")
                    buf = buf[2:]
                    text_grid_height = int.from_bytes(buf[:2], byteorder="little")
                    buf = buf[2:]

                    char_cell_height = buf[:1]
                    buf = buf[1:]
                    char_cell_width = buf[:1]
                    buf = buf[1:]

                    text_foreground_color_index = buf[:1]
                    buf = buf[1:]
                    text_background_color_index = buf[:1]
                    buf = buf[1:]

                    plain_text_data = ""
                    sub_block_size = fab.read(1)[0]
                    while True:
                        plain_text_data += fab.read(sub_block_size).decode("ascii")

                        sub_block_size = fab.read(1)[0]
                        if(sub_block_size == 0):
                            break

                    print("plain_text_data:\n" + plain_text_data)

                    buf = fab.read(1)[0]

                #application extension
                if(fab.read(1)[0] != 0xFF):
                    fab.seek(-1, 1)
                else:
                    buf = fab.read(1)[0]
                    if(buf != 11):
                        sys.exit("block size in application extension is not 11")
                    buf = fab.read(buf)
                    if(len(buf) != 11):
                        sys.exit("size of application extension is not 11")

                    application_identifier = buf[:8].decode("ascii")
                    buf = buf[8:]
                    application_identifier_code = buf[:3]
                    buf = buf[3:]

                    application_data = b""
                    sub_block_size = fab.read(1)[0]
                    while True:
                        application_data += fab.read(sub_block_size)

                        sub_block_size = fab.read(1)[0]
                        if(sub_block_size == 0):
                            break

                    buf = fab.read(1)[0]
            """


            # image descriptor
            if (buf != b"\x2c"):
                sys.exit("image separator is not 0x2C")

            image_left_position = int.from_bytes(fab.read(2), byteorder="little")
            image_top_position = int.from_bytes(fab.read(2), byteorder="little")
            image_width = int.from_bytes(fab.read(2), byteorder="little")
            image_height = int.from_bytes(fab.read(2), byteorder="little")

            buf = bin(int.from_bytes(fab.read(1), byteorder="little"))[2:].zfill(8)

            local_color_table_flag = bool(int(buf[0]))
            interlace_flag = bool(int(buf[1]))
            sort_flag = bool(int(buf[2]))
            size_of_local_table = int(buf[5:], 2)


            # local color table
            if (local_color_table_flag):
                for i in range((2 ** (size_of_local_table + 1)) * 3):
                    local_color_table.append(int.from_bytes(fab.read(1), byteorder="little"))
            
            local_color_table_flags.append(int(local_color_table_flag))
            if (local_color_table_flag):
                local_color_tables.append(local_color_table)
            else:
                local_color_tables.append(0)

            # skip image data
            frames += 1
            print("skip image", frames)
            fab.seek(1, 1)
            block_size = int.from_bytes(fab.read(1), byteorder="little")

            while block_size != 0:
                fab.seek(block_size, 1)
                block_size = int.from_bytes(fab.read(1), byteorder="little")

            # for the next loop
            buf = fab.read(1)

            """
            # image data
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
            
            buf = ""
            while True:
                sub_block = fab.read(sub_block_size)
                for i in range(len(sub_block)):
                    buf = bin(int(sub_block[i]))[2:].zfill(8) + buf

                while(len(buf) > code_size):
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

                sub_block_size = fab.read(1)[0]
                if(sub_block_size == 0):
                    break
            """

    if (export_gif_data):
        with open("gif_data.js", "w") as f:
            gif_data =  f"let {logical_screen_height = }\n"
            gif_data += f"let {logical_screen_width = }\n"
            gif_data += f"let global_color_table_flag = {int(global_color_table_flag)};\n"
            gif_data += f"let {global_color_table = };\n"
            gif_data += f"let {frames = }\n"
            gif_data += f"let {local_color_table_flags = };\n"
            gif_data += f"let {local_color_tables = };\n"
            f.write(gif_data)


def main():
    if(len(sys.argv) == 2):
        file_path = sys.argv[1]
        if (os.path.isfile(file_path)):
            gif(file_path, True)
        else:
            sys.exit("given path is not a file")


if (__name__ == "__main__"):
    main()