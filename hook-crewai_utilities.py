from PyInstaller.utils.hooks import collect_data_files

# Coletar todos os arquivos de tradução do pacote crewai.utilities
datas = collect_data_files('crewai.utilities', subdir='../translations')


