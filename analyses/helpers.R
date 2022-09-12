getGlasgow <- function() {
  glasgowNorms <- read_csv('../data/norming/GlasgowNorms.csv') %>%
    mutate(word = case_when(word == 'bunk (bed)' ~ 'bunkbed',
                            word == 'absurd' ~ 'absurdity',
                            word == 'defiant' ~ 'defiance',
                            word == 'admire' ~ 'admiration',
                            word == 'adore' ~ 'adoration',
                            word == 'clear' ~ 'clarity',
                            word == 'complex' ~ 'complexity',
                            word == 'crazy' ~ 'craziness',
                            word == 'diverse' ~ 'diversity',
                            word == 'divine' ~ 'divinity',
                            word == 'elegant' ~ 'elegance',
                            word == 'friendly' ~ 'friendliness',
                            word == 'inflame' ~ 'inflamation',
                            word == 'modest' ~ 'modesty',
                            word == 'mystery' ~ 'mysterious',
                            word == 'obvious' ~ 'obviousness',
                            word == 'odd' ~ 'oddity',
                            word == 'peculiar' ~ 'peculiarity',
                            word == 'playful' ~ 'playfulness',
                            word == 'positive' ~ 'positivity',
                            word == 'random' ~ 'randomness',
                            word == 'real' ~ 'reality',
                            word == 'reassure' ~ 'reassurance',
                            word == 'relieved' ~ 'relief',
                            word == 'shy' ~ 'shyness',
                            word == 'thoughtless' ~ 'thoughtlessness',
                            word == 'vague' ~ 'vagueness',
                            word == 'vicious' ~ 'viciousness',
                            word == 'weary' ~ 'weariness',
                            TRUE ~ word)) %>%
    select(word, CNC, IMAG) %>%
    rename(concreteness = CNC,
           imageability = IMAG)
  return(glasgowNorms)
}
