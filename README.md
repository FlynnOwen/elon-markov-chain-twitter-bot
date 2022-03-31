<h1 align="center"> [Elon Markov Chain Twitter Bot](!https://twitter.com/elonstorybot) :bird: </h1> 
<p align="center"> Ever wondered what Elon Musk would sound like if he started quoting childrens books halfway through his Tweets? Wonder no longer! </p>
<h2 align="center"> What is it? </h2>
<img align="left" height=250 src="img/twitter.png"/>

<br>
<p align="center"> 
  Upon running of the lambda function (markov_tweet.py), all Elon Musks Tweets are scraped, cleaned and concatenated with a large dataset of childrens books. 
  
  From here, a first order Markov Chain is generated, and words are recursively generated from this Markov Chain until either the Twitter word limit or a sentence conclusion is reached.
</p>
<br>
<h2 align="center"> Markov What?! </h2>

<img align="right" height=350 src="img/markov_chain.png"/>
<p align="center"> 
  A Markov Chain is a stochastic model that describes a sequence of events. We call an event the transitioning of a state. Events must satisfy the Markov Property - meaning that the probability of the next state transition depends only on current or previous states. In Figure 1, our states are the nodes A & E. Events are given by the orange edges - with state transition probabilities in black.
  
  In this example, we are considering only a first order Markov Chain - this means that we only care about the current state of the chain. In math-y terms:

  ```math
    P(x_{t+1} | x_t, x_{t-1}, ..., x_1) = P(x_{t+1} | x_t)
  ```
  
  Here, our 'sequence' is a large string of words combined between Elon Musk's Tweets, and a collection of childrens books. We consider words as our 'states', and our transition probabilities are the proportion of times that a word comes directly succeeding another word. For example, if the word "Tesla" has occured 50 times in our large string, and 20 of the times it occured, the direct succeeding word was "rocks!", our transition probability between "Tesla" and "rocks!" would be 20/50 or 0.4.
</p>
