## Get statistics of articles

import glob
paths = glob.glob("data/*")

if __name__=="__main__":

    """Print categories, subcategories & number of files to file"""

    print("Collecting stats. Saving to 'categories.txt' ...")
    with open("categories.txt", "w") as f:
        for path in paths:
            f.write(path.replace("data/", "") + "\n")
            for subcat in glob.glob(path + "/*"):
                # Get number of files
                nfiles = len(glob.glob(subcat + "/*"))
                f.write("\t" + subcat.replace("data/", "") + "\t[==>]\t" + str(nfiles) + "\n")
