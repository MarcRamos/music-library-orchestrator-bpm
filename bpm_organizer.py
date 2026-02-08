def bpm_folder(bpm):
    if bpm < 100:
        return "100 or less"
    if 100 <= bpm < 140:
        return "100-140"
    if 140 <= bpm < 180:
        return "140-180"
    if 180 <= bpm < 200:
        return "180-200"
    if 200 <= bpm <= 260:
        return "200-260"
    else:
        return "260 or more"

