import os, hashlib
from PeerPack import KurrentParser

class PeerCore:
    def __init__(self, c2t):
        self.KUrrentLIST = {}
        self.c2t = c2t
        self.parser = KurrentParser.Parser()

    def closeEvent(self):
        print('close')
        # save status

    def getHash(self, dir, fNames):
        sha = hashlib.sha256()

        for fName in fNames:
            try:
                file = open(dir + fName, "rb")
            except IOError:
                pass
            while True:
                buf = file.read(8196)
                if not buf:
                    break
                sha.update(buf)
            file.close()
        return sha

    def piece_exist(self, hash, piece_num):
        return False

    def get_piece(self, hash, piece_num):
        return None

    def get_todolist(self):
        return []

    def make_torrent(self, file_name, sharing_dir, tracker_text):
        f = open(file_name, "w", encoding='utf-8')
        tll = tracker_text.splitlines()
        tracker_list = []
        flist = self.get_file_list_recur(sharing_dir + os.path.sep, "")
        sha = self.getHash(sharing_dir, flist)
        f.write(sha.hexdigest() + "\n")

        for i in tll:
            if len(i.strip()) > 0:
                tracker_list.append(i.strip())

        f.write("trackers : " + str(len(tracker_list)) + "\n")

        for i in tracker_list:
            f.write(i.strip() + "\n")

        f.write("files : " + str(len(flist)) + "\n")
        for i in flist:
            f.write(i + "\n")
            f.write(str(os.path.getsize(sharing_dir + i)) + "\n")

        f.close()

        f = open(file_name, 'rt')
        self.add_seeder(tracker_list, f)
        f.close()

        self.KUrrentLIST[sha] = {'file_name': file_name, 'saving_dir': sharing_dir,
                                       'tracker': tracker_list, 'status': 'complete'}

    def get_file_list_recur(self, abs_path, file):
        if os.path.isfile(abs_path+file):
            if os.path.basename(abs_path+file).startswith("."):
                return None
            return file
        elif os.path.isdir(abs_path+file):
            child = os.listdir(abs_path+file)
            ret = []
            for i in child:
                f = self.get_file_list_recur(abs_path, file + os.path.sep + i)
                if f is None:
                    continue
                if type(f) is str:
                    ret.append(f)
                elif type(f) is list:
                    for j in f:
                        ret.append(j)
            return ret

    def add_torrent(self, file_name, saving_dir, tracker_text):
        kurrent_file = open(file_name, 'rt')
        file_hash = self.parser.get_file_hash(kurrent_file)
        tracker_list = self.parser.parse_tracker_text(tracker_text)
        kurrent_file.close()

        self.add_download_list(file_hash, tracker_list)

        self.KUrrentLIST[file_hash] = {'file_name' : file_name, 'saving_dir' : saving_dir,
                                       'tracker' : tracker_list, 'status' : 'downloading'}

    def add_download_list(self, file_hash, tracker_list):
        for tracker in tracker_list:
            self.c2t.add_request(tracker, file_hash)

    def add_seeder(self, tracker_list, kurrent_file):
        file_hash = self.parser.get_file_hash(kurrent_file)
        for tracker in tracker_list:
            self.c2t.add_seeder_request(tracker, file_hash)

    def get_seeder_num(self, hash):
        return ""

    def get_torrent_table(self):
        torrent_table = []

        for i in self.KUrrentLIST.keys():
            t = [i, self.KUrrentLIST[i]['file_name'], self.KUrrentLIST[i]['saving_dir'],
                 self.KUrrentLIST[i]['status'], self.get_seeder_num(i)]
            torrent_table.append(t)

        return torrent_table
