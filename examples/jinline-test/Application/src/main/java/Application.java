import edu.ucla.cs.onr.test.*;

public class Application {
	public int doubleOrSquare(int num, boolean dbl) {
    Squarer lib;
    if(dbl)
      lib = new Doubler();
    else
      lib = new Squarer();

		return lib.doIt(num);
	}
};
