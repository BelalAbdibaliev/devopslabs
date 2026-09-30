import os
import glob

dockerfiles = glob.glob("src/*/Dockerfile")

for df in dockerfiles:
    with open(df, "r") as f:
        content = f.read()
    
    if "COPY Directory.Build.props" not in content:
        # Insert after WORKDIR /src
        content = content.replace("WORKDIR /src\n", "WORKDIR /src\nCOPY Directory.Build.props .\n")
        
        with open(df, "w") as f:
            f.write(content)
