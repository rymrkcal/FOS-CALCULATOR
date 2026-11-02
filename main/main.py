from Input.inputs import collect
from Output.output import save_and_show

def main():
    saved = collect()
    if saved == None:
        return
    
    save_and_show(saved)
 
if __name__ == "__main__":
    main()
