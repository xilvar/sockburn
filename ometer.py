# -*- coding: utf-8 -*-

import os, time, json

MIN_HINT_ITERATIONS = 100

class OMeter(object):
  def __init__(self,unit="iterations",max_iterations=None,logger=None):
    self.unit = unit
    self.t0 = time.time()
    self.t_last = self.t0
    self.logger = logger
    self.iterations = 0
    self.max_iterations = max_iterations
    self.total_it = 0
    self.rate_buckets = []
    self.hint_ips = 0
    def _out_fn(s):
      if self.logger:
        self.logger.info(s)
      else:
        print(s)
    self.out_fn = _out_fn
  
  def write_hint(self, hint_name):
    td = self.t_last-self.t0
    if self.total_it >= MIN_HINT_ITERATIONS:
      fi = open(hint_name+".hint", "wb")
      json.dump({"iterations":self.total_it, "time":td}, fi)
    else:
      print "not writing hint : %d %d" % (self.total_it, td)

  def read_hint(self, hint_name):
    try:
      hint_obj = json.load(open(hint_name+".hint"))
      self.hint_ips = hint_obj["iterations"] / hint_obj["time"]
    except:
      pass
  
  def set_max_iterations(self, i):
    self.max_iterations = i

  def iteration(self, num=1, force_output=False):
    self.iterations += num
    self.total_it += num
    t_new = time.time()
    td = t_new-self.t_last
    if (td > 1.0) or force_output:
      rate = self.iterations/td
      self.rate_buckets.insert(0,rate)
      if len(self.rate_buckets) > 100:
        self.rate_buckets.pop()
      avg_rate = sum(self.rate_buckets)/len(self.rate_buckets)
      if self.max_iterations:
        if self.hint_ips:
          rate = self.hint_ips if self.hint_ips else avg_rate 
        eta = (self.max_iterations-self.total_it) / rate
      else:
        eta = 0.0
      hours = int(eta/60/60)
      mins = int((eta - hours*60*60)/60)
      secs = eta % 60
      
      elapsed = t_new-self.t0
      e_hours = int(elapsed/60/60)
      e_mins = int((elapsed - e_hours*60*60)/60)
      e_secs = elapsed % 60
      
      self.out_fn("%d:\t%.4f %s/s\t(eta: %dh %dm %ds) (elapsed: %dh %dm %ds)" % (self.total_it, avg_rate, self.unit, hours, mins, secs, e_hours, e_mins, e_secs))
      self.iterations = 0
      self.t_last = t_new

  def force_output(self):
    self.iteration(num=0, force_output=True)
