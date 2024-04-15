echo off
@<"list.txt" (for /f "delims=" %%i in ('more') do @copy nul "%%~i")
