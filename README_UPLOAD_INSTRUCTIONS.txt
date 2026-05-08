Y90 Publication Database v5.5 hard category save fix

Upload these files to the ROOT of your GitHub Pages repo and replace the old files:
1. index.html
2. publications.json

Important check:
After upload, open the website and look at the footer. It should show:
Radioembolization Literature Management · v5.5 · Hard Category Save Fix

Test workflow:
1. Edit one publication category.
2. Click Save Publication.
3. Refresh the page. It should remain changed.
4. Click Export JSON. It must download a file named publications.json.
5. Upload that publications.json to GitHub root and replace the old one.
6. Open the website in Incognito mode to confirm the GitHub copy is updated.

If the footer still says v5.0.1 / v5.4 / anything else, GitHub Pages is still serving the old index.html or the file was uploaded to the wrong location/branch.
