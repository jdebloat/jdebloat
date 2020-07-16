import edu.ucla.cs.onr.test.Library;

public class Application {
	public static void main(String[] args) {
    System.out.println(new Application().square(2));
		return;
	}

  public int square(int num) {
    Library lib = new Library();
    return lib.square(num);
  }
};
