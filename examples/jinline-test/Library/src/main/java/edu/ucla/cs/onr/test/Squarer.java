package edu.ucla.cs.onr.test;

public class Squarer extends Doer {
  public void bar(int val) {
  }
  @Override
  public int doIt(int val) {
    int result = val * val;
    return result;
  }
}
