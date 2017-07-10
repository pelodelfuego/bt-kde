Bt-kde
======

BallTree KDE is a perf oriented implementation of kernel density estimation.<br>
While performing prediction of probabilities on a lot en entries,<br>
I realized classical implementation does not scale well with the number of points.<br>

This implementation takes advantage of the sparsity of the distribution to address this problematic.


## Algorithm
This implementation use the BallTree property to 'fuzzy index' the distribution with a custom metric in order to cluster points together.<br>
It reduce the number of queries and ponderate the result by the size of each cluster.<br>
This approximation is valid only if the points are dense enough regarding to the kernel bandwidth.<br>

It is especially adapted for prediction on sparse distributions.

Only the Gaussian kernel is implemented at the moment.

## Visually speaking

Performing a KDE is actually equivalent to convolve the distribution by the kernel.<br>

When points of the distribution are close enough regarding to the kernel bandwidth,<br>
We can compute only one ponderated kernel and assume the result will be almost equal to the sum of the 2 kernels.

![](https://raw.githubusercontent.com/pelodelfuego/bt-kde/master/img/visual_def.gif)

* *Green:* exact curve
* *Blue:* approximated curve
* *Red:* absolute error

**Note:** Here is a 1D example, in N dimensions, the closeness of points is evaluated by an ellipse equation.<br>
It allows to use different bandwidth on each dimensions.



## Formally speaking

![](https://raw.githubusercontent.com/pelodelfuego/bt-kde/master/img/formal_def.gif)

This is also true for aggregation of N points. In such a case, the kernel would be ponderated by N.


## Conclusion

As always, the tradeoff we are making here depends on the nature of the data,<br>
but having a few concentrated clusters make this approximation suitable.<br>
Depending on the precision needed, it is also possible to tweak the metric so it aggregate smaller clusters.

At this cost, we dropped the perf by a factor ~20 (mode details on the demo notebook).

This experiment highlight the versatility of BallTree which allow bunch of application with a custom metric.
(PS: it is awesome !)

We can also note, it is possible to use different bandwidth on each dimensions.<br>


