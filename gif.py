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
    disposal_method = -1
    user_input_flag = None
    transparent_color_flag = None
    delay_time = 0
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
    local_color_tables = []
    image_pos = []
    image_size = []
    disposal_methods = []
    transparent_color_indexs = []
    delays = []
    index_streams = []


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
        # x3B end of file
        while buf != b"\x3B":
            print("frame", frames)
            # skip extentions
            # while buf != b"\x00":
            #     if (buf == b"\x21"):
            #         print("skip extention:", fab.read(1))
            #         while buf != 0:
            #             buf = int.from_bytes(fab.read(1), byteorder="little")
            #             fab.seek(buf, 1)
            #         buf = fab.read(1)
            #     else:
            #         break

            while buf == b"\x21":
                buf = fab.read(1)
                #print("extention:", buf)

                # graphic control extension
                if (buf == b"\xF9"):
                    buf = int.from_bytes(fab.read(1), byteorder="little")
                    if (buf != 4):
                        sys.exit("block size in graphic control extension is not 4")

                    buf = fab.read(buf)

                    another_buf = bin(int.from_bytes(buf[0:1], byteorder="little"))[2:].zfill(8)
                    disposal_method = int(another_buf[3:6], 2)
                    user_input_flag = bool(int(another_buf[6]))
                    transparent_color_flag = bool(int(another_buf[7]))

                    delay_time = int.from_bytes(buf[1:3], byteorder="little")
                    transparent_color_index = int.from_bytes(buf[3:4], byteorder="little")
                    if (fab.read(1) != b"\x00"):
                        sys.exit("block terminator in graphic control extension not found")

                    buf = fab.read(1)

                # comment extension
                if (buf == b"\xFE"):
                    comment_data = ""
                    sub_block_size = int.from_bytes(fab.read(1), byteorder="little")
                    while sub_block_size != 0:
                        comment_data += fab.read(sub_block_size).decode("ascii", errors="ignore")
                        sub_block_size = int.from_bytes(fab.read(1), byteorder="little")

                    print("comment_data:\n" + comment_data)

                    buf = fab.read(1)

                # plain text extension
                # TODO seems this block placed after image data and can work as image data (using delay time and render text on top past frame)
                if (buf == b"\x01"):
                    buf = int.from_bytes(fab.read(1), byteorder="little")
                    if (buf != 12):
                        sys.exit("block size in plain text extension is not 12")

                    buf = fab.read(buf)

                    text_grid_left_pos = int.from_bytes(buf[:2], byteorder="little")
                    text_grid_top_pos = int.from_bytes(buf[2:4], byteorder="little")

                    text_grid_width = int.from_bytes(buf[4:6], byteorder="little")
                    text_grid_height = int.from_bytes(buf[6:8], byteorder="little")

                    char_cell_height = buf[8:9]
                    char_cell_width = buf[9:10]

                    text_foreground_color_index = buf[10:11]
                    text_background_color_index = buf[11:12]

                    plain_text_data = ""
                    sub_block_size = int.from_bytes(fab.read(1), byteorder="little")
                    while sub_block_size != 0:
                        plain_text_data += fab.read(sub_block_size).decode("ascii", errors="ignore")
                        sub_block_size = int.from_bytes(fab.read(1), byteorder="little")

                    print("plain_text_data:\n" + plain_text_data)

                    buf = fab.read(1)

                # application extension
                if (buf == b"\xFF"):
                    buf = int.from_bytes(fab.read(1), byteorder="little")
                    if (buf != 11):
                        sys.exit("block size in application extension is not 11")

                    buf = fab.read(buf)

                    application_identifier = buf[:8].decode("ascii", errors="ignore")
                    application_identifier_code = buf[8:]

                    application_data = b""
                    sub_block_size = int.from_bytes(fab.read(1), byteorder="little")
                    while sub_block_size != 0:
                        application_data += fab.read(sub_block_size)
                        sub_block_size = int.from_bytes(fab.read(1), byteorder="little")

                    buf = fab.read(1)

                if (buf == b"\x2C"):
                    break

            # end of file
            # i had one gif thats ends with comment extentions
            if (buf == b"\x3B"):
                break


            # image descriptor
            if (buf != b"\x2C"):
                sys.exit("image separator is not 0x2C")

            image_left_pos = int.from_bytes(fab.read(2), byteorder="little")
            image_top_pos = int.from_bytes(fab.read(2), byteorder="little")
            image_width = int.from_bytes(fab.read(2), byteorder="little")
            image_height = int.from_bytes(fab.read(2), byteorder="little")

            buf = bin(int.from_bytes(fab.read(1), byteorder="little"))[2:].zfill(8)

            local_color_table_flag = bool(int(buf[0]))
            interlace_flag = bool(int(buf[1]))
            sort_flag = bool(int(buf[2]))
            size_of_local_table = int(buf[5:], 2)


            # local color table
            if (local_color_table_flag):
                local_color_table = []
                for i in range((2 ** (size_of_local_table + 1)) * 3):
                    local_color_table.append(int.from_bytes(fab.read(1), byteorder="little"))

            # skip image data
            # frames += 1
            # print("skip image", frames)
            # fab.seek(1, 1)
            # block_size = int.from_bytes(fab.read(1), byteorder="little")

            # while block_size != 0:
            #     fab.seek(block_size, 1)
            #     block_size = int.from_bytes(fab.read(1), byteorder="little")

            # image data
            lzw_minimal_code_size = int.from_bytes(fab.read(1), byteorder="little")

            color_table_size = 2 ** lzw_minimal_code_size

            image_data = ""
            sub_block_size = int.from_bytes(fab.read(1), byteorder="little")
            while sub_block_size != 0:
                for i in range(sub_block_size):
                    image_data = bin(int.from_bytes(fab.read(1), byteorder="little"))[2:].zfill(8) + image_data
                sub_block_size = int.from_bytes(fab.read(1), byteorder="little")

            chk_frame = -1

            if (frames == chk_frame):
                print(image_data)
                print(color_table_size, lzw_minimal_code_size)

            CLR_pos = 2 ** lzw_minimal_code_size
            EOI_pos = CLR_pos + 1
            
            code_table = {}
            code_stream = []
            index_stream = []

            code_size = lzw_minimal_code_size + 1
            init = False
            while True:
                if (frames == chk_frame):
                    print(image_data[-code_size:], int(image_data[-code_size:], 2))
                current_code = int(image_data[-code_size:], 2)
                image_data = image_data[:-code_size]
                code_stream.append(current_code)

                if (frames == chk_frame):
                    print(len(code_table), 2 ** code_size - 1)

                if (init):
                    index_stream.append(code_table[current_code])
                    init = False
                    continue

                if (current_code == EOI_pos):
                    break

                if (current_code == CLR_pos):
                    code_table = {}
                    for i in range(color_table_size):
                        code_table[i] = ([i])

                    code_table[CLR_pos] = ("CLR")
                    code_table[EOI_pos] = ("EOI")
                    code_size = lzw_minimal_code_size + 1
                    init = True
                    continue
                
                if (len(code_table) == 2 ** code_size - 1):
                    if (code_size >= 12):
                        code_size = 12
                    else:
                        code_size += 1

                # prev code
                # code_stream[-2]

                if(current_code in code_table):
                    index_stream.append(code_table[current_code])
                    code_table[len(code_table)] = code_table[code_stream[-2]].copy()
                    code_table[len(code_table) - 1].append(code_table[current_code][0])
                else:
                    index_stream.append(code_table[code_stream[-2]].copy())
                    index_stream[-1].append(code_table[code_stream[-2]][0])
                    code_table[len(code_table)] = code_table[code_stream[-2]].copy()
                    code_table[len(code_table) - 1].append(code_table[code_stream[-2]][0])


            if (local_color_table_flag):
                local_color_tables.append(local_color_table)
            else:
                local_color_tables.append(-1)

            disposal_methods.append(disposal_method)

            if (transparent_color_flag):
                transparent_color_indexs.append(transparent_color_index)
            else:
                transparent_color_indexs.append(-1)

            delays.append(delay_time)

            image_pos.append([image_left_pos, image_top_pos])
            image_size.append([image_width, image_height])

            if(frames == chk_frame):
                print(index_stream)

            buf = []
            for i in range(len(index_stream)):
                for b in range (len(index_stream[i])):
                    buf.append(index_stream[i][b])

            index_streams.append(buf)
            #print(index_streams)

            if(image_height * image_width != len(buf)):
                print("index_stream is too short", frames)

            #print(interlace_flag)

            # for the next loop
            buf = fab.read(1)
            frames += 1


    if (export_gif_data):
        with open("gif_data.js", "w") as f:
            gif_data =  f"let {logical_screen_height = };\n"
            gif_data += f"let {logical_screen_width = };\n"
            gif_data += f"let global_color_table_flag = {int(global_color_table_flag)};\n"
            gif_data += f"let {background_color_index = };\n"
            gif_data += f"let {global_color_table = };\n"
            gif_data += f"let {frames = };\n"
            gif_data += f"let {local_color_tables = };\n"
            gif_data += f"let {disposal_methods = };\n"
            gif_data += f"let {transparent_color_indexs = };\n"
            gif_data += f"let {delays = };\n"
            gif_data += f"let {image_pos = };\n"
            gif_data += f"let {image_size = };\n"
            gif_data += f"let {index_streams = };\n"
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