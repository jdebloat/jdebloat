import edu.ucla.cs.onr.test.*;

public class Application {
	public static void main(String[] args) {
    Library lib;
    if(args[0].equals("a"))
      lib = new Library();
    else
      lib = new Library_Child();

    System.out.println(new Application().square(2, lib));
		return;
	}

  public int square(int num, Library lib) {
    return lib.square(num);
  }
};
