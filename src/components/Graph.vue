<template>
  <div class="graph">
    <svg version="1.1"  style="width:100%;height:100%;position:fixed;top:0;left:0;bottom:0;right:0;" xmlns="http://www.w3.org/2000/svg">
    </svg>
  </div>
</template>

<script>
import 'whatwg-fetch'
import _ from 'lodash'

var timingRequest = fetch('/static/timing.json').then(resp => resp.json())
var networkInRequest = fetch('/static/network-in.json').then(resp => resp.json())

let absoluteStart = null;
let timing = null;
let timingIndices = {}
let timingAnimationStart = null;
let networkIn = null;
let networkInAnimationStart = null;

var drawTiming = (animationOffset) => {
  // depends on `timing` and `networkIn` above
  if (!timingAnimationStart) {
    timingAnimationStart = animationOffset
  }
  var animationTimestamp = absoluteStart + (timingAnimationStart - animationOffset)
  debugger
  _.map(timing, (dataPoints, entityName) => {
    var [requestTimestamp, requestDuration] = dataPoints[timingIndices[entityName]]
    if (animationTimestamp >= requestTimestamp) {
      timingIndices[entityName] += 1
    }
  })
  // window.requestAnimationFrame(drawTiming)
}

var drawNetworkIn = (timestamp) => {
  // depends on `timing` and `networkIn` above
  debugger
}

export default {
  route: {
    activate: () => {
      Promise.all([timingRequest, networkInRequest]).then(([timingInner, networkInDataInner]) => {
        _.map(Object.keys(timingInner), entityName => {
          timingIndices[entityName] = 0;
        })
        timing = timingInner
        networkIn = networkInDataInner.Datapoints
        absoluteStart = new Date(networkInDataInner.Datapoints[0].Timestamp).getTime()
        var drawTimingAnimId = window.requestAnimationFrame(drawTiming)
        setTimeout(() => {
          window.cancelAnimationFrame(drawTimingAnimId)
        }, 1000)
        // window.requestAnimationFrame(drawNetworkIn)
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1 {
  color: #42b983;
}
</style>
