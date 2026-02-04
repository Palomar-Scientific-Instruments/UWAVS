#!/usr/bin/env python3

import argparse

CHORD_NAMES = ['GAA0', 'GAB0', 'GAC0', 'GAD0']

# def change_chord_name(src_path: str, dst_path: str, chord_name: str):
def change_chord_name(src_path: str, dst_path: str):
    '''
    Changes the chord name in a Signals and Components csv file.

    Inputs:
        src_path   (str) - Absolute path to source csv file
        dst_path   (str) - Absolute path to csv file in which
                           contain the new chord name
        chord_name (str) - New chord name (i.e. If we want to
                           change from GAD0 to GBD0, then
                           chord_name = GBD0)
    '''
    with open(src_path, "r") as ifile:
        raw_lines = ifile.readlines()

    new_lines = raw_lines[0]
    for chord_name in CHORD_NAMES:
        for line in raw_lines[1:]:
            tokens = line.strip().split(',')

            if (len(tokens[0]) > 0):
                # Change signal ID
                new_name = tokens[0]
                if (tokens[0][0] != '-'):
                    old_name = tokens[0].split('-')
                    new_name = f'{"-".join(old_name[0:2])}-{chord_name}-{"-".join(old_name[3:])}'

                # Change signal name
                new_sig = tokens[1]
                if (tokens[1] != "TBD"):
                    old_sig = tokens[1].split('-')
                    new_sig = f'{old_sig[0][0:2]}{chord_name}-{"-".join(old_sig[1:])}'

                # Chane component name
                new_comp = tokens[2]
                if (new_comp[0:2] == '55'):
                    old_comp = tokens[2].split('-')
                    new_comp = f'{old_comp[0][0:2]}{chord_name}-{"-".join(old_comp[1:])}'

                # Change cubicle name
                new_cub = tokens[8]
                if (new_cub[0:2] == '55'):
                    old_cub = tokens[8].split('-')
                    new_cub = f'{old_cub[0][0:2]}{chord_name}-{"-".join(old_cub[1:])}'

                # Putting everything together
                line_chunk1 = ','.join(tokens[3:8]) # 1st chunk of columns that don't change
                line_chunk2 = ','.join(tokens[9:])  # 2nd chunk of columns that don't change
                line_cur = f'{new_name},{new_sig},{new_comp},{line_chunk1},{new_cub},{line_chunk2}\n'
                new_lines += line_cur

    with open(dst_path, 'w') as ofile:
        ofile.write(new_lines)

    return

def main():
    descript = '''Changes the name of a chord in a "Signals and Components" sheed. Note,
                  this application takes a csv as an input. Thus, you should convert your
                  "Signals and Components" sheet to a csv file'''
#    nme_help = '''New name of chord'''
    src_help = '''Absolute path to csv file in which the chord name will be changed'''
    dst_help = '''Absolute path to oupt csv file which will contain the new chord name'''

    parser = argparse.ArgumentParser(description = descript)
#    parser.add_argument('NAME', help = nme_help)
    parser.add_argument('SRC', help = src_help)
    parser.add_argument('DST', help = dst_help)

    # Create list of keys to the args dictionary
    args = parser.parse_args().__dict__

#    change_chord_name(args['SRC'], args['DST'], args['NAME'])
    change_chord_name(args['SRC'], args['DST'])

    return

######################################### main ###########################################
if (__name__ == '__main__'):
    main()

