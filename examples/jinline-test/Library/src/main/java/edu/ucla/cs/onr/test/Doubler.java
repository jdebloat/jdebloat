package edu.ucla.cs.onr.test;

public class Doubler extends Doer {
  public void foo(int val) {
  }
  @Override
  public int doIt(int val) {
    int result = val * 2;
    return result;
  }
}
