"""
Sentence Generator using Markov Chains. I wrote the code, not the docstrings.
"""

import numpy as np

class SentenceGenerator(object):
    """Markov chain creator for simulating bad English.

    Attributes:
        (what attributes do you need to keep track of?)

    Example:
        >>> yoda = SentenceGenerator("Yoda.txt")
        >>> print(yoda.babble())
        The dark side of loss is a path as one with you.
    """
    def __init__(self, filename):
        """Read the specified file and build a transition matrix from its
        contents. You may assume that the file has one complete sentence
        written on each line.
        """
        with open(filename, 'r', encoding="utf8") as fs:
            self.sentences = list()
            unique = set()
            line = fs.readline().strip()
            
            while line:
                self.sentences.append(line) # Adds the lines to the sentence attributes
                unique.update(line.split()) # Adds the words to a set
                
                line = fs.readline().strip() # Gets the next line
                
                
            n = len(unique) # Number of unique words
            self.transition = np.zeros((n+2,n+2)) # Initializes the transition matrix
            
            self.unique_words = list()
            self.unique_words.append("$tart")
            
            states = dict()
            states["$tart"] = 0
            states["$top"] = n+1
            self.transition[states["$top"],states["$top"]] = 1
            
            for x in self.sentences:
                
                sentence = x.split()
                
                s = len(states)-1 # Gets the current length of the states list
                first = sentence[0]
                if first not in states.keys():
                    states[first] = s  # Adds first word to dictionary if not already there
                    self.unique_words.append(first)
                self.transition[states["$tart"],states[first]] += 1 # Adds first word of sentence to transition matrix
                # print("Added $tart", first, "at position", states["$tart"], states[first])
                    
                s = len(states)-1 # Gets the current length of the states list
                i = 0
                for w in range(len(sentence)-1): # Stops before end of sentence
                    curr = sentence[w]
                    after_curr = sentence[w+1]
                    if curr not in states.keys():
                        states[curr]=i+s  # Maps words to the next index
                        self.unique_words.append(curr)
                        i += 1
                    if after_curr not in states.keys():
                        states[after_curr]=i+s  # Maps words to the next index
                        self.unique_words.append(after_curr)
                        i += 1
                    self.transition[states[curr], states[after_curr]] += 1
                    # print("Added", curr, after_curr, "at position", states[curr], states[after_curr])
                    
                s = len(states)-1 # Gets the current length of the states list
                last = sentence[-1]
                if last not in states.keys():
                    states[last] = s  # Adds last word to dictionary if not already there
                    self.unique_words.append(last)
                self.transition[states[last],states["$top"]] += 1 # Adds first word of sentence to transition matrix
        
        self.states = states
        self.unique_words.append("$top")        
        self.transition = self.transition / np.sum(self.transition, axis = 1).reshape((len(self.transition),-1))


                
    def babble(self):
        """Begin at the start sate and use the strategy from
        four_state_forecast() to transition through the Markov chain.
        Keep track of the path through the chain and the corresponding words.
        When the stop state is reached, stop transitioning and terminate the
        sentence. Return the resulting sentence as a single string.
        """
        sentence = ""
        i = np.argmax(np.random.multinomial(1,self.transition[0,:]))
        sentence += self.unique_words[i] + " "
        
        while i != self.states["$top"]:
            i = np.argmax(np.random.multinomial(1,self.transition[i,:]))
            if self.unique_words[i] != "$top":
                sentence += self.unique_words[i] + " "
            
        return sentence.strip()
