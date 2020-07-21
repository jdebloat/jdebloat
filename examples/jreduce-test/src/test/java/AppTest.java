import org.junit.Test;

import static org.junit.Assert.assertEquals;
import java.io.IOException;

public class AppTest {

  @Test
  public void getGreetingTest() throws Exception {
    assertEquals("Hello, A!", Main.getGreeting("A"));
  }

}
