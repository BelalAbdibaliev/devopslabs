import os
import glob

dockerfiles = glob.glob("src/*/Dockerfile")

for df in dockerfiles:
    with open(df, "r") as f:
        content = f.read()
    
    # Replace the manual user creation with the built-in 'app' user
    old_text = """# Non-root user for security
RUN adduser -u 1000 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser"""
    
    new_text = """# Use built-in non-root user provided by modern .NET images
USER app"""
    
    content = content.replace(old_text, new_text)
    
    with open(df, "w") as f:
        f.write(content)
