from gui import Geppetto, ChooseConfigFile
import sys

if __name__ == "__main__":
    try:
        ChooseConfigFile().run()
    except Exception as e:
        sys.exit(0)
    try:
        Geppetto().run()
    except Exception as e:
        sys.exit(0)
