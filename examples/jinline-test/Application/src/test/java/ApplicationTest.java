import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;
import java.io.IOException;

public class ApplicationTest {
  @Test public void squareTest() {
    Application app = new Application();
    assertEquals(app.square(2), 4);
  }
};
