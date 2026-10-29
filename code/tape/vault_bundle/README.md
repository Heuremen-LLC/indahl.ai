# VAULT sealing bundle

`/vault/tlock.js` on indahl.ai is `entry.js` bundled with tlock-js 0.9.0 and esbuild 0.21.5. To rebuild and compare:

    npm init -y && npm i tlock-js@0.9.0 esbuild@0.21.5 buffer
    npx esbuild entry.js --bundle --minify --platform=browser --target=es2020 --define:global=globalThis --format=iife --outfile=tlock.bundle.js

The chain hash and public key of the drand quicknet are fixed in the code, so the browser checks every drand answer against them even though the requests pass through indahl.ai.
