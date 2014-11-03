class HunterMeta(object):
  """ Some meta info that can't go into a Hunter object due to
      recursion problems
      
      Hunter has (1) meta (2) stats.
      The meta object is passed to the stats
      The hunter object is passed to spell methods
  """
  race = 'Night Elf'
  talent4 = 0
  talent5 = 0
  talent6 = 0
  talent7 = 0
  spec = 0 # 0=BM, 1=MM, 2=SV
  glyphs = []
  enchants = ''