public class Main {

  public static String getGreeting(String name) throws Exception {
    return Main.class.getClassLoader().loadClass(name).newInstance().toString();
  }

  public static void main(String[] args) throws Exception {
    System.out.println(getGreeting(args[0]));
  }
}
