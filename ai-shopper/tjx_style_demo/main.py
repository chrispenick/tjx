from .quiz import Quiz
from .catalog import load_or_buildCatalog
from .llm import prefilter, compose_outfit

def main():
    q=Quiz(season='fall',vibe='cozy',palette='neutrals',budget=100)
    cat=load_or_buildCatalog()
    s=prefilter(cat,q)
    print(compose_outfit(q,s))

if __name__=='__main__': main()
