import edu.ucla.cs.onr.test.*;

public class Application {
  public static int doubleOrSquare(int val, boolean isDouble) {
    Doer doer = null;
    if (isDouble) {
      Doubler doubler = new Doubler();
      doubler.foo(val % 2);
      doer = doubler;
    }
    else {
      Squarer squarer = new Squarer();
      squarer.bar(val * 3 + 4);
      doer = squarer;
    }

    if (val > 100) {
      val = 100;
    }
    else if (val < 0) {
      val = 0;
    }

    int result = doer.doIt(val);
    return result;
  }
}
