
def parse_start_stop_fields(l0_name, start_pos, field_len):
    print(l0_name)
    start = l0_name[start_pos:start_pos+field_len]
    start_pos += field_len + 1
    stop = l0_name[start_pos:start_pos+field_len]
    return start, stop

