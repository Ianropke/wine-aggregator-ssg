#!/usr/bin/env bash

# Dette script flytter pagefind-filer til den korrekte Vercel output mappe
# for at undgå 404 fejl på statiske ressourcer under produktion.

echo "Running Vercel Pagefind Fix..."

if [ -d "dist/pagefind" ]; then
    echo "Found dist/pagefind. Copying to .vercel/output/static/pagefind..."
    mkdir -p .vercel/output/static
    cp -r dist/pagefind .vercel/output/static/
    echo "Done!"
else
    echo "Warning: dist/pagefind not found. Did pagefind run successfully?"
fi
